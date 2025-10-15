import { ImprovedResult } from '@/components/common/resume_previewer_context';

const API_URL = process.env.NEXT_PUBLIC_API_URL!;

/** Uploads job descriptions and returns a job_id */
export async function uploadJobDescriptions(
    descriptions: string[],
    resumeId: string
): Promise<string> {
    const res = await fetch(`${API_URL}/api/v1/jobs/upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_descriptions: descriptions, resume_id: resumeId }),
    });
    if (!res.ok) throw new Error(`Upload failed with status ${res.status}`);
    const data = await res.json();
    console.log('Job upload response:', data);
    return data.job_id[0];
}

/** Improves the resume and returns the full preview object */
export async function improveResume(
    resumeId: string,
    jobId: string
): Promise<ImprovedResult> {
    let response: Response;
    try {
        response = await fetch(`${API_URL}/api/v1/resumes/improve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resume_id: resumeId, job_id: jobId }),
        });
    } catch (networkError) {
        console.error('Network error during improveResume:', networkError);
        throw networkError;
    }

    const text = await response.text();
    if (!response.ok) {
        console.error('Improve failed response body:', text);
        
        // 解析错误信息，提供更友好的错误提示
        let errorMessage = `Improve failed with status ${response.status}`;
        try {
            const errorData = JSON.parse(text);
            if (errorData.detail) {
                if (errorData.detail.includes('Parsing of job with ID')) {
                    errorMessage = '工作描述解析失败，请尝试重新上传工作描述或检查工作描述格式。';
                } else if (errorData.detail.includes('Keyword extraction failed for job')) {
                    errorMessage = '无法从工作描述中提取关键词，请确保工作描述包含足够的职位要求和技能信息，然后重新上传。';
                } else if (errorData.detail.includes('Keyword extraction failed for resume')) {
                    errorMessage = '无法从简历中提取关键词，请重新上传简历。';
                } else if (errorData.detail.includes('Resume not found')) {
                    errorMessage = '简历未找到，请重新上传简历。';
                } else if (errorData.detail.includes('Job not found')) {
                    errorMessage = '工作描述未找到，请重新上传工作描述。';
                } else {
                    errorMessage = errorData.detail;
                }
            }
        } catch (parseError) {
            // 如果无法解析 JSON，使用原始错误信息
            errorMessage = text;
        }
        
        throw new Error(errorMessage);
    }

    let data: ImprovedResult;
    try {
        data = JSON.parse(text) as ImprovedResult;
    } catch (parseError) {
        console.error('Failed to parse improveResume response:', parseError, 'Raw response:', text);
        throw parseError;
    }

    console.log('Resume improvement response:', data);
    return data;
}