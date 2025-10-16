// File: apps/frontend/app/dashboard/page.tsx


'use client';

import React from 'react';
import BackgroundContainer from '@/components/common/background-container';
import JobListings from '@/components/dashboard/job-listings';
import ResumeAnalysis from '@/components/dashboard/resume-analysis';
import Resume from '@/components/dashboard/resume-component'; // rename import to match default export
import { useResumePreview } from '@/components/common/resume_previewer_context';
// import { analyzeJobDescription } from '@/lib/api/jobs';

interface AnalyzedJobData {
	title: string;
	company: string;
	location: string;
}


export default function DashboardPage() {
	const { improvedData } = useResumePreview();
	console.log('Dashboard - Improved Data:', improvedData);
	
	if (!improvedData) {
		return (
			<BackgroundContainer className="min-h-screen" innerClassName="bg-zinc-950">
				<div className="flex items-center justify-center h-full p-6 text-gray-400">
					No improved resume found. Please click "Improve" on the Job Upload page first.
				</div>
			</BackgroundContainer>
		);
	}

	const { data } = improvedData;
	console.log('Dashboard - Data object:', data);
	
	const { resume_preview, new_score } = data;
	console.log('Dashboard - resume_preview:', resume_preview);
	console.log('Dashboard - new_score:', new_score);
	
	// 确保使用真实的简历数据，如果没有则显示错误
	if (!resume_preview) {
		console.error('Dashboard - resume_preview is null or undefined');
		return (
			<BackgroundContainer className="min-h-screen" innerClassName="bg-zinc-950">
				<div className="flex flex-col items-center justify-center h-full p-6 text-gray-400">
					<p className="text-xl mb-4">No resume data found.</p>
					<p className="text-sm">The server did not return resume preview data. Please check the console for details.</p>
					<p className="text-xs mt-4">Debug info: {JSON.stringify(data, null, 2)}</p>
				</div>
			</BackgroundContainer>
		);
	}
	
	const preview = resume_preview;
	const newPct = Math.round(new_score * 100);

	const handleJobUpload = async (): Promise<AnalyzedJobData | null> => {
		if (!data.job_id) {
			console.error('No job_id available in improvedData');
			return null;
		}

		try {
			const res = await fetch(
				`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs?job_id=${encodeURIComponent(data.job_id)}`
			);
			if (!res.ok) {
				console.error('Failed to fetch job data:', res.status, res.statusText);
				return null;
			}

			const jobResponse = await res.json();
			const jobData = jobResponse.data?.processed_job;

			if (!jobData) {
				console.error('No processed_job data in response:', jobResponse);
				return null;
			}

			// Map backend job data to AnalyzedJobData format
			return {
				title: jobData.job_title || 'Unknown Position',
				company: jobData.company_profile?.company_name || 'Unknown Company',
				location: jobData.location?.city ? 
					`${jobData.location.city}${jobData.location.state ? ', ' + jobData.location.state : ''}` : 
					'Not specified',
			};
		} catch (error) {
			console.error('Error fetching job data:', error);
			return null;
		}
	};


	return (
		<BackgroundContainer className="min-h-screen" innerClassName="bg-zinc-950 backdrop-blur-sm overflow-auto">
			<div className="w-full h-full overflow-auto py-8 px-4 sm:px-6 lg:px-8">
				{/* Header */}
				<div className="container mx-auto">
					<div className="mb-10">
						<h1 className="text-3xl font-semibold pb-2 text-white">
							Your{' '}
							<span className="bg-gradient-to-r from-pink-400 to-purple-400 text-transparent bg-clip-text">
								Resume Matcher
							</span>{' '}
							Dashboard
						</h1>
						<p className="text-gray-300 text-lg">
							Manage your resume and analyze its match with job descriptions.
						</p>
					</div>

					{/* Grid: left = analyzer + analysis, right = resume */}
					<div className="grid grid-cols-1 md:grid-cols-3 gap-8">
						{/* Left column */}
						<div className="space-y-8">
							<section>
								<JobListings onLoadJob={handleJobUpload} />
							</section>
							<section>
								<ResumeAnalysis
									score={newPct}
									details={improvedData.data.details ?? ''}
									commentary={improvedData.data.commentary ?? ''}
									improvements={improvedData.data.improvements ?? []}
								/>
							</section>
						</div>

						{/* Right column */}
						<div className="md:col-span-2">
							<div className="bg-gray-900/70 backdrop-blur-sm p-6 rounded-lg shadow-xl h-full flex flex-col border border-gray-800/50">
								<div className="mb-6">
									<h2 className="text-2xl font-bold text-white mb-1">Your Resume</h2>
									<p className="text-gray-400 text-sm">
										This is your resume. Update it via the resume upload page.
									</p>
								</div>
								<div className="flex-grow overflow-auto">
									<Resume resumeData={preview} />
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</BackgroundContainer>
	);
}