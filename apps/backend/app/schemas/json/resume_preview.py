SCHEMA = {
    "personalInfo": {
        "name": "string",
        "title": "string | null",
        "email": "string",
        "phone": "string",
        "location": "string | null",
        "website": "string | null",
        "linkedin": "string | null",
        "github": "string | null",
    },
    "summary": "string | null",
    "experience": [
        {
            "id": 0,
            "title": "string",
            "company": "string | null",
            "location": "string | null",
            "years": "string | null",
            "description": ["string"],
        }
    ],
    "education": [
        {
            "id": 0,
            "institution": "string",
            "degree": "string",
            "years": "string | null",
            "description": "string | null",
        }
    ],
    "skills": ["string"],
}
