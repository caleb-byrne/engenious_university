# Docker & CI/CD Setup for AI Red Team Testing

## Local Testing Commands

```bash
# 1. Quick test with our custom script
./test-docker.sh

# 2. Using Docker directly
cd promptfoo
docker build -f Red-Teaming/Dockerfile.redteam -t promptfoo-redteam ./Red-Teaming
docker run --rm --env-file Red-Teaming/.env -v "$(pwd)/Red-Teaming/output:/app/output" promptfoo-redteam

# 3. Using Docker Compose
docker-compose up promptfoo-redteam

# 4. Development mode with shell access
docker-compose --profile dev up promptfoo-dev

# 5. View results in browser
docker-compose --profile viewer up results-viewer
# Then open http://localhost:8080
```

## CI/CD Pipeline Setup

### GitHub Actions
1. Add `OPENAI_API_KEY` to GitHub Secrets:
   - Go to Settings → Secrets and variables → Actions
   - Add new secret: `OPENAI_API_KEY` with your API key
   - The workflow in `.github/workflows/ai-red-team.yml` will run automatically

### GitLab CI
```yaml
# .gitlab-ci.yml
stages:
  - security-test

ai-red-team-test:
  stage: security-test
  image: docker:24
  services:
    - docker:24-dind
  before_script:
    - cd promptfoo
  script:
    - docker build -f Red-Teaming/Dockerfile.redteam -t promptfoo-redteam ./Red-Teaming
    - mkdir -p Red-Teaming/output
    - docker run --rm -e OPENAI_API_KEY="$OPENAI_API_KEY" -v "$(pwd)/Red-Teaming/output:/app/output" promptfoo-redteam
  artifacts:
    paths:
      - promptfoo/Red-Teaming/output/
    expire_in: 1 week
  variables:
    DOCKER_DRIVER: overlay2
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    
    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
    }
    
    stages {
        stage('Build & Test') {
            steps {
                dir('promptfoo') {
                    sh '''
                        docker build -f Red-Teaming/Dockerfile.redteam -t promptfoo-redteam ./Red-Teaming
                        mkdir -p Red-Teaming/output
                        docker run --rm -e OPENAI_API_KEY="$OPENAI_API_KEY" -v "$(pwd)/Red-Teaming/output:/app/output" promptfoo-redteam
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'promptfoo/Red-Teaming/output/**/*', fingerprint: true
                }
            }
        }
    }
}
```

## Verification Checklist

- ✅ Docker builds successfully
- ✅ Container runs without errors
- ✅ API key loaded from environment
- ✅ Results generated in output directory
- ✅ CI/CD pipeline configured
- ✅ Security secrets properly managed

## Troubleshooting

### Build Issues
- Ensure Docker Desktop is running
- Check that you're in the `promptfoo` directory
- Verify the Dockerfile path: `Red-Teaming/Dockerfile.redteam`

### Runtime Issues
- Verify API key is set in `Red-Teaming/.env`
- Check API rate limits and quotas
- Ensure output directory has write permissions

### CI/CD Issues
- Verify secrets are properly configured
- Check that the workflow file is in `.github/workflows/`
- Ensure repository has necessary permissions for Docker operations