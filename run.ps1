rm -r output
docker build -t confl-bot .
docker run -it --rm -v ${pwd}/output:/app/output --name confl-bot confl-bot