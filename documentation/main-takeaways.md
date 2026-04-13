Things learned:

-using multiple requirements.txt files per container

-more work with multi-container stacks
-building multiple custom docker images in one repo
-building non python containers
-making multi-build docker images

-intro to GitHub Actions
-branch protection
-creating CI pipeline to run linting and test on actions like a push or PR
-running jobs in parallel or waiting for other jobs to complete

-creating a CD pipeline to build docker images to GHCR and then SSH and deploy them
-waiting for full pipelines to finish before proceeding

-using multiple docker-compose files

-github secrets
-generating token for CI/CD
-need to use Tailscale auth key so CD can SSH into the server
-creating an evironment in GitHub and storing variables/secrets for deployment