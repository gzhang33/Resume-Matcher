export interface MissingField {
  field: string;
  label: string;
  type: 'text' | 'textarea' | 'email' | 'phone';
  required: boolean;
  placeholder?: string;
}

export interface ResumeData {
  personal_data?: {
    firstName?: string;
    lastName?: string;
    email?: string;
    phone?: string;
    linkedin?: string;
    portfolio?: string;
    location?: {
      city?: string;
      country?: string;
    };
  };
  experiences?: Array<{
    jobTitle?: string;
    company?: string;
    location?: string;
    startDate?: string;
    endDate?: string;
    description?: string[];
  }>;
  education?: Array<{
    institution?: string;
    degree?: string;
    fieldOfStudy?: string;
    startDate?: string;
    endDate?: string;
  }>;
}

export function detectMissingInfo(resumeData: ResumeData): MissingField[] {
  const missingFields: MissingField[] = [];
  
  // Check personal data
  if (!resumeData.personal_data?.firstName) {
    missingFields.push({
      field: 'firstName',
      label: 'First Name',
      type: 'text',
      required: true,
      placeholder: 'Enter your first name'
    });
  }
  
  if (!resumeData.personal_data?.lastName) {
    missingFields.push({
      field: 'lastName',
      label: 'Last Name',
      type: 'text',
      required: true,
      placeholder: 'Enter your last name'
    });
  }
  
  if (!resumeData.personal_data?.email) {
    missingFields.push({
      field: 'email',
      label: 'Email Address',
      type: 'email',
      required: true,
      placeholder: 'Enter your email address'
    });
  }
  
  if (!resumeData.personal_data?.phone) {
    missingFields.push({
      field: 'phone',
      label: 'Phone Number',
      type: 'phone',
      required: false,
      placeholder: 'Enter your phone number (optional)'
    });
  }
  
  if (!resumeData.personal_data?.location?.city) {
    missingFields.push({
      field: 'city',
      label: 'City',
      type: 'text',
      required: false,
      placeholder: 'Enter your city (optional)'
    });
  }
  
  if (!resumeData.personal_data?.location?.country) {
    missingFields.push({
      field: 'country',
      label: 'Country',
      type: 'text',
      required: false,
      placeholder: 'Enter your country (optional)'
    });
  }
  
  // Check if there are any experiences
  if (!resumeData.experiences || resumeData.experiences.length === 0) {
    missingFields.push({
      field: 'experience',
      label: 'Work Experience',
      type: 'textarea',
      required: false,
      placeholder: 'Describe your work experience (optional)'
    });
  } else {
    // Check if first experience has company
    const firstExp = resumeData.experiences[0];
    if (!firstExp.company) {
      missingFields.push({
        field: 'company',
        label: 'Company Name',
        type: 'text',
        required: false,
        placeholder: 'Enter your current or most recent company'
      });
    }
  }
  
  // Check education
  if (!resumeData.education || resumeData.education.length === 0) {
    missingFields.push({
      field: 'education',
      label: 'Education',
      type: 'textarea',
      required: false,
      placeholder: 'Describe your education background (optional)'
    });
  }
  
  return missingFields;
}

export function mergeMissingInfo(originalData: ResumeData, missingInfo: Record<string, string>): ResumeData {
  const updatedData = { ...originalData };
  
  // Update personal data
  if (!updatedData.personal_data) {
    updatedData.personal_data = {};
  }
  
  if (missingInfo.firstName) {
    updatedData.personal_data.firstName = missingInfo.firstName;
  }
  
  if (missingInfo.lastName) {
    updatedData.personal_data.lastName = missingInfo.lastName;
  }
  
  if (missingInfo.email) {
    updatedData.personal_data.email = missingInfo.email;
  }
  
  if (missingInfo.phone) {
    updatedData.personal_data.phone = missingInfo.phone;
  }
  
  if (!updatedData.personal_data.location) {
    updatedData.personal_data.location = {};
  }
  
  if (missingInfo.city) {
    updatedData.personal_data.location.city = missingInfo.city;
  }
  
  if (missingInfo.country) {
    updatedData.personal_data.location.country = missingInfo.country;
  }
  
  // Add experience if provided
  if (missingInfo.experience) {
    if (!updatedData.experiences) {
      updatedData.experiences = [];
    }
    if (updatedData.experiences.length === 0) {
      updatedData.experiences.push({
        jobTitle: 'Professional Experience',
        company: missingInfo.company || 'Various Companies',
        description: [missingInfo.experience],
        startDate: '2020-01-01',
        endDate: 'Present'
      });
    }
  }
  
  // Add education if provided
  if (missingInfo.education) {
    if (!updatedData.education) {
      updatedData.education = [];
    }
    if (updatedData.education.length === 0) {
      updatedData.education.push({
        institution: 'Educational Institution',
        degree: 'Degree',
        description: missingInfo.education,
        startDate: '2018-01-01',
        endDate: '2022-01-01'
      });
    }
  }
  
  return updatedData;
}
