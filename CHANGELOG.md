# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-14

### Added
- AI Features:
    - Introduced pydantic schema for structured output in exam content generation.
    - Added generate_exam_questions API tests.
    - Handled refusals in the exam content generation.
    - Updated question options list in template.

### Changed
- Renamed qgenform.html to qugen.html for better alignment with naming conventions.
- Updated URL path from q-gen/ to qugen/ for consistency.
- Reduced max_length of the subject field for improved validation and performance.

## [0.1.0] - 2025-01-01

### Added

- Initial project structure and configuration slightly modified from the Cookiecutter-Django template.
- CI configuration for GitHub Actions, including linting, automated testing, and coverage targets.
- Basic documentation including this CHANGELOG, CONTRIBUTING guidelines, and the project's goals in the README.
- LICENSE file with a permissive open-source license.
- Basic Django app with a working integration with OpenAI API, featuring a minimal chat completion feature.
- Tests for AI app views and URLs and an overall 93% test coverage for the project.
- Successfully built for Docker with a multi-stage Dockerfile.
- Successfully deployed to Heroku with a PostgreSQL database.
