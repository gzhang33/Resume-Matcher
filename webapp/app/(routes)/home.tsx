"use client";

import ThirdPartyServicesKeys from "@/components/third-party-services/third-party-services";
import ResumeGlance from "@/components/resume/resume-glance/resume-glance";
import JobDescriptions from "@/components/job-descriptions/job-descriptions";
import VectorScore from "@/components/vector-scores/vector-scores";
import CommonWords from "@/components/common-words/common-words";
import Suggestions from "@/components/suggestions/suggestions";
import FileUpload from "@/components/resume/file-upload/file-upload";
import Hero from "@/components/hero/hero";
import Footer from "../_components/footer/footer";

export default function Home() {
  return (
    <main className="text-white">
      <Hero>
        <ThirdPartyServicesKeys />
        <FileUpload buttonLabel="Upload Your Resume" />
      </Hero>
      <ResumeGlance />
      <JobDescriptions />
      <VectorScore />
      <CommonWords />
      <Suggestions />
      <Footer />
    </main>
  );
}
