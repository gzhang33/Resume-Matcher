import uuid
import json
import logging
import re

from typing import List, Dict, Any, Optional
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent import AgentManager
from app.prompt import prompt_factory
from app.schemas.json import json_schema_factory
from app.models import Job, Resume, ProcessedJob
from app.schemas.pydantic import StructuredJobModel
from .exceptions import JobNotFoundError

logger = logging.getLogger(__name__)


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.json_agent_manager = AgentManager()
    
    def _extract_title_from_text(self, text: str) -> str:
        """
        Try to extract a reasonable job title directly from the raw text.
        Strategy:
        - Use the first non-empty line that looks like a short title (<= 120 chars)
        - Prefer lines with 2-10 words and minimal punctuation
        - Fallback to the first ~80 chars of the text (still derived from user input)
        - Never introduce hardcoded business data. If nothing can be extracted, return empty string.
        """
        if not text:
            logger.warning("No text provided for title extraction; returning empty title")
            return ""

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        title_candidate = ""

        # Heuristic 1: first short line, limited punctuation, reasonable word count
        for ln in lines:
            if len(ln) <= 120:
                # Count words and punctuation density
                words = ln.split()
                if 1 <= len(words) <= 12:
                    # Limit heavy punctuation lines
                    punct_ratio = sum(ch in ",.;:!/?|" for ch in ln) / max(len(ln), 1)
                    if punct_ratio < 0.1:
                        title_candidate = ln
                        break

        # Heuristic 2: fallback to first 80 chars from text (still user-provided)
        if not title_candidate:
            snippet = text.strip()[:80]
            title_candidate = snippet

        # Final cleanup: collapse spaces
        title_candidate = re.sub(r"\s+", " ", title_candidate).strip()
        return title_candidate

    def _extract_fallback_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from job description using dynamic text analysis.
        All keywords are extracted from the actual text - NO hardcoded keywords.
        
        Uses multiple extraction strategies:
        1. Capitalized terms (likely proper nouns, technologies)
        2. Quoted terms (explicitly important)
        3. Noun phrases from requirements/qualifications sections
        4. Terms following key indicators (experience with, knowledge of, etc.)
        """
        if not text or len(text.strip()) < 10:
            logger.warning("Text too short for keyword extraction")
            return []
        
        keywords = set()
        
        # Strategy 1: Extract capitalized words/phrases (2+ chars)
        # These are often technologies, frameworks, companies, acronyms
        capitalized_pattern = r'\b[A-Z][A-Za-z0-9]*(?:[.\-/][A-Za-z0-9]+)*\b'
        capitalized_matches = re.findall(capitalized_pattern, text)
        for match in capitalized_matches:
            if len(match) >= 2 and match not in ['The', 'A', 'An', 'In', 'On', 'At', 'To', 'For', 'And', 'Or', 'But', 'If', 'Our', 'We', 'You', 'Your', 'This', 'That', 'These', 'Those']:
                keywords.add(match)
        
        # Strategy 2: Extract quoted terms
        quoted_pattern = r'["\']([^"\']+)["\']'
        quoted_matches = re.findall(quoted_pattern, text)
        for match in quoted_matches:
            if 2 <= len(match) <= 50:
                keywords.add(match.strip())
        
        # Strategy 3: Extract terms after key phrases (experience with, knowledge of, etc.)
        key_phrases = [
            r'experience (?:with|in|using)\s+([A-Za-z0-9\s,/\-\.]+?)(?:\.|,|\n|and|or|\bfor\b)',
            r'knowledge of\s+([A-Za-z0-9\s,/\-\.]+?)(?:\.|,|\n|and|or)',
            r'proficiency in\s+([A-Za-z0-9\s,/\-\.]+?)(?:\.|,|\n|and|or)',
            r'familiar(?:ity)? with\s+([A-Za-z0-9\s,/\-\.]+?)(?:\.|,|\n|and|or)',
            r'skills?(?:\s+in)?[:\s]+([A-Za-z0-9\s,/\-\.]+?)(?:\.|,|\n{2})',
            r'(?:requires?|required)[:\s]+([A-Za-z0-9\s,/\-\.]+?)(?:\.|,|\n{2})',
        ]
        
        for pattern in key_phrases:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                phrase = match.group(1).strip()
                # Split by common separators
                items = re.split(r'\s*[,;/]\s*|\s+and\s+|\s+or\s+', phrase)
                for item in items:
                    item = item.strip()
                    if 2 <= len(item) <= 50:
                        keywords.add(item)
        
        # Strategy 4: Extract degree mentions with context
        degree_pattern = r"(Bachelor'?s?|Master'?s?|PhD|Doctorate|BSc|MSc|BA|MA|B\.S\.|M\.S\.)\s*(?:degree)?\s*(?:in)?\s*([A-Za-z\s]+?)(?:\.|,|or|\n)"
        degree_matches = re.finditer(degree_pattern, text, re.IGNORECASE)
        for match in degree_matches:
            degree_type = match.group(1).strip()
            field = match.group(2).strip() if match.group(2) else ''
            if degree_type:
                keywords.add(degree_type)
            if field and len(field) > 2:
                keywords.add(field.strip())
        
        # Strategy 5: Extract year requirements
        year_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)?'
        year_matches = re.finditer(year_pattern, text, re.IGNORECASE)
        for match in year_matches:
            keywords.add(f"{match.group(1)}+ years")
        
        # Strategy 6: Extract hyphenated technical terms
        hyphenated_pattern = r'\b[A-Za-z]+-[A-Za-z]+(?:-[A-Za-z]+)*\b'
        hyphenated_matches = re.findall(hyphenated_pattern, text)
        for match in hyphenated_matches:
            if len(match) >= 5:
                keywords.add(match)
        
        # Clean and filter keywords
        filtered_keywords = set()
        for keyword in keywords:
            # Remove very short or very long keywords
            if 2 <= len(keyword) <= 50:
                # Remove pure numbers
                if not keyword.isdigit():
                    # Remove common words that aren't useful
                    if keyword.lower() not in ['will', 'can', 'may', 'must', 'should', 'would', 'could', 'shall', 'need', 'able', 'have', 'has', 'had', 'get', 'got', 'make', 'made']:
                        filtered_keywords.add(keyword.strip())
        
        # Convert to sorted list and limit
        result = sorted(list(filtered_keywords))[:100]  # Increase limit to 100
        logger.info(f"Dynamic keyword extraction found {len(result)} keywords from text")
        if result:
            logger.debug(f"Sample keywords: {result[:10]}")
        return result

    async def create_and_store_job(self, job_data: dict) -> List[str]:
        """
        Stores job data in the database and returns a list of job IDs.
        """
        resume_id = str(job_data.get("resume_id"))

        if not await self._is_resume_available(resume_id):
            raise AssertionError(
                f"resume corresponding to resume_id: {resume_id} not found"
            )

        job_ids = []
        for job_description in job_data.get("job_descriptions", []):
            job_id = str(uuid.uuid4())
            job = Job(
                job_id=job_id,
                resume_id=str(resume_id),
                content=job_description,
            )
            self.db.add(job)

            await self._extract_and_store_structured_job(
                job_id=job_id, job_description_text=job_description
            )
            logger.info(f"Job ID: {job_id}")
            job_ids.append(job_id)

        await self.db.commit()
        return job_ids

    async def _is_resume_available(self, resume_id: str) -> bool:
        """
        Checks if a resume exists in the database.
        """
        query = select(Resume).where(Resume.resume_id == resume_id)
        result = await self.db.scalar(query)
        return result is not None

    async def _extract_and_store_structured_job(
        self, job_id, job_description_text: str
    ):
        """
        extract and store structured job data in the database
        """
        structured_job = await self._extract_structured_json(job_description_text)
        if not structured_job:
            logger.error(f"Structured job extraction failed for job_id: {job_id}")
            # 使用动态文本分析提取关键词
            fallback_keywords = self._extract_fallback_keywords(job_description_text)
            
            if not fallback_keywords:
                logger.error(f"Dynamic keyword extraction found no keywords for job_id: {job_id}")
                logger.error(f"Job description preview: {job_description_text[:200]}...")
                # 不使用任何硬编码的默认关键词，返回空数组
                fallback_keywords = []
            
            # 创建基本的 ProcessedJob 记录
            dynamic_title = self._extract_title_from_text(job_description_text)
            processed_job = ProcessedJob(
                job_id=job_id,
                job_title=dynamic_title,
                job_summary=job_description_text[:500] + "..." if len(job_description_text) > 500 else job_description_text,
                extracted_keywords=json.dumps({"extracted_keywords": fallback_keywords})
            )
            self.db.add(processed_job)
            await self.db.flush()
            await self.db.commit()
            
            if fallback_keywords:
                logger.info(f"Created fallback ProcessedJob with {len(fallback_keywords)} extracted keywords for job_id: {job_id}")
            else:
                logger.warning(f"Created ProcessedJob with NO keywords for job_id: {job_id} - resume improvement may fail")
            return job_id

        # 检查并确保关键词不为空
        extracted_keywords = structured_job.get("extracted_keywords", [])
        if not extracted_keywords or len(extracted_keywords) == 0:
            logger.warning(f"AI parsing succeeded but no keywords extracted for job_id: {job_id}, using dynamic extraction")
            extracted_keywords = self._extract_fallback_keywords(job_description_text)
            if not extracted_keywords:
                logger.error(f"Dynamic keyword extraction also found no keywords for job_id: {job_id}")
                logger.error(f"Job description preview: {job_description_text[:200]}...")
                # 不使用硬编码的默认值，返回空数组
                extracted_keywords = []
        
        processed_job = ProcessedJob(
            job_id=job_id,
            job_title=structured_job.get("job_title"),
            company_profile=json.dumps(structured_job.get("company_profile"))
            if structured_job.get("company_profile")
            else None,
            location=json.dumps(structured_job.get("location"))
            if structured_job.get("location")
            else None,
            date_posted=structured_job.get("date_posted"),
            employment_type=structured_job.get("employment_type"),
            job_summary=structured_job.get("job_summary"),
            key_responsibilities=json.dumps(
                {"key_responsibilities": structured_job.get("key_responsibilities", [])}
            )
            if structured_job.get("key_responsibilities")
            else None,
            qualifications=json.dumps(structured_job.get("qualifications", []))
            if structured_job.get("qualifications")
            else None,
            compensation_and_benfits=json.dumps(
                structured_job.get("compensation_and_benfits", [])
            )
            if structured_job.get("compensation_and_benfits")
            else None,
            application_info=json.dumps(structured_job.get("application_info", []))
            if structured_job.get("application_info")
            else None,
            extracted_keywords=json.dumps(
                {"extracted_keywords": extracted_keywords}
            ),
        )

        self.db.add(processed_job)
        await self.db.flush()
        await self.db.commit()

        return job_id

    async def _extract_structured_json(
        self, job_description_text: str
    ) -> Dict[str, Any] | None:
        """
        Uses the AgentManager+JSONWrapper to ask the LLM to
        return the data in exact JSON schema we need.
        """
        try:
            prompt_template = prompt_factory.get("structured_job")
            prompt = prompt_template.format(
                json.dumps(json_schema_factory.get("structured_job"), indent=2),
                job_description_text,
            )
            logger.info(f"Structured Job Prompt: {prompt}")
            raw_output = await self.json_agent_manager.run(prompt=prompt)

            try:
                structured_job: StructuredJobModel = StructuredJobModel.model_validate(
                    raw_output
                )
            except ValidationError as e:
                logger.error(f"Validation error: {e}")
                error_details = []
                for error in e.errors():
                    field = " -> ".join(str(loc) for loc in error["loc"])
                    error_details.append(f"{field}: {error['msg']}")
                
                logger.error(f"Validation error details: {'; '.join(error_details)}")
                logger.error(f"Raw AI output: {raw_output}")
                return None
            return structured_job.model_dump(mode="json", by_alias=False)
        except Exception as e:
            logger.error(f"AI agent error during job parsing: {e}")
            logger.error(f"Job description text: {job_description_text[:200]}...")
            return None

    async def get_job_with_processed_data(self, job_id: str) -> Optional[Dict]:
        """
        Fetches both job and processed job data from the database and combines them.

        Args:
            job_id: The ID of the job to retrieve

        Returns:
            Combined data from both job and processed_job models

        Raises:
            JobNotFoundError: If the job is not found
        """
        job_query = select(Job).where(Job.job_id == job_id)
        job_result = await self.db.execute(job_query)
        job = job_result.scalars().first()

        if not job:
            raise JobNotFoundError(job_id=job_id)

        processed_query = select(ProcessedJob).where(ProcessedJob.job_id == job_id)
        processed_result = await self.db.execute(processed_query)
        processed_job = processed_result.scalars().first()

        combined_data = {
            "job_id": job.job_id,
            "raw_job": {
                "id": job.id,
                "resume_id": job.resume_id,
                "content": job.content,
                "created_at": job.created_at.isoformat() if job.created_at else None,
            },
            "processed_job": None
        }

        if processed_job:
            combined_data["processed_job"] = {
                "job_title": processed_job.job_title,
                "company_profile": json.loads(processed_job.company_profile) if processed_job.company_profile else None,
                "location": json.loads(processed_job.location) if processed_job.location else None,
                "date_posted": processed_job.date_posted,
                "employment_type": processed_job.employment_type,
                "job_summary": processed_job.job_summary,
                "key_responsibilities": json.loads(processed_job.key_responsibilities).get("key_responsibilities", []) if processed_job.key_responsibilities else None,
                "qualifications": json.loads(processed_job.qualifications).get("qualifications", []) if processed_job.qualifications else None,
                "compensation_and_benfits": json.loads(processed_job.compensation_and_benfits).get("compensation_and_benfits", []) if processed_job.compensation_and_benfits else None,
                "application_info": json.loads(processed_job.application_info).get("application_info", []) if processed_job.application_info else None,
                "extracted_keywords": json.loads(processed_job.extracted_keywords).get("extracted_keywords", []) if processed_job.extracted_keywords else None,
                "processed_at": processed_job.processed_at.isoformat() if processed_job.processed_at else None,
            }

        return combined_data
