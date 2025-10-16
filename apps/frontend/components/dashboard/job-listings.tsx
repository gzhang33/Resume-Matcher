import React, { useState } from 'react';
import PasteJobDescription from './paste-job-description';

interface Job {
	// Assuming id might be optional or not returned by analysis for a single display
	id?: number;
	title: string;
	company: string;
	location: string;
	// description?: string; // Raw description is input, not necessarily stored on this Job type after analysis
}

// Type for the data expected from the analysis backend
type AnalyzedJobData = Pick<Job, 'title' | 'company' | 'location'>;

interface JobListingsProps {
	// Callback to load job data
	onLoadJob: () => Promise<AnalyzedJobData | null>;
}

const JobListings: React.FC<JobListingsProps> = ({ onLoadJob }) => {
	const [isModalOpen, setIsModalOpen] = useState(false);
	const [analyzedJob, setAnalyzedJob] = useState<AnalyzedJobData | null>(null);
	const [isAnalyzing, setIsAnalyzing] = useState(false);
	const [isLoading, setIsLoading] = useState(true);
	// Optional: add error state for analysis failures
	// const [error, setError] = useState<string | null>(null);

	// Auto-load job data on mount
	React.useEffect(() => {
		const loadJob = async () => {
			setIsLoading(true);
			try {
				const jobData = await onLoadJob();
				setAnalyzedJob(jobData);
				if (!jobData) {
					console.warn('No job data available.');
				}
			} catch (err) {
				console.error('Error loading job data:', err);
				setAnalyzedJob(null);
			} finally {
				setIsLoading(false);
			}
		};
		loadJob();
	}, [onLoadJob]);

	const handleOpenModal = () => {
		// setError(null); // Clear previous errors when opening modal
		setIsModalOpen(true);
	};
	const handleCloseModal = () => setIsModalOpen(false);

	// Removed - not needed in dashboard as jobs are already analyzed

	// truncateText function removed as it's no longer used

	return (
		<div className="bg-gray-900/80 backdrop-blur-sm p-6 rounded-lg shadow-xl border border-gray-800/50">
			<h2 className="text-2xl font-bold text-white mb-1">Job Analysis</h2>
			<p className="text-gray-400 mb-6 text-sm">
				{analyzedJob
					? 'Job details matched in your resume improvement.'
					: 'Loading job details...'}
			</p>
			{isLoading ? (
				<div className="text-center text-gray-400 py-8">
					<p>Loading job details...</p>
				</div>
			) : analyzedJob ? (
				<div className="space-y-4">
					<div
						// key is not needed for a single item display
						className="p-4 bg-gray-700 rounded-md shadow-md"
					>
						<h3 className="text-lg font-semibold text-gray-100">{analyzedJob.title}</h3>
						<p className="text-sm text-gray-300">{analyzedJob.company}</p>
						<p className="text-xs text-gray-400 mt-1">{analyzedJob.location}</p>
					</div>
				</div>
			) : (
				<div className="text-center text-gray-400 py-8 flex flex-col justify-center items-center">
					{/* Optional: Display error message here if setError is implemented */}
					{/* {error && <p className="text-red-400 mb-3">{error}</p>} */}
					<p className="mb-3">No job description data available.</p>
					<p className="text-xs">The job data could not be loaded from your previous analysis.</p>
				</div>
			)}
		</div>
	);
};

export default JobListings;
