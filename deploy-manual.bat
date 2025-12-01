@echo off
aws ecr get-login-password --region ap-southeast-7 --profile ecr | docker login --username AWS --password-stdin 685863266308.dkr.ecr.ap-southeast-7.amazonaws.com

docker buildx build --platform=linux/arm64 -t prefect-worker .

docker tag prefect-worker:latest 685863266308.dkr.ecr.ap-southeast-7.amazonaws.com/zentrix/prefect-worker:latest
docker push 685863266308.dkr.ecr.ap-southeast-7.amazonaws.com/zentrix/prefect-worker:latest