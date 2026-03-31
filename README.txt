Pour lancer le docker:

docker compose up -d --build



Pour accéder au projet:

http://localhost:5173


Pour accéder à kafkaUi:

modifier le networks de kafkaUi dans le dockercompose par:

    networks:
      - exposed
      - micro_network

puis aller sur:

http://localhost:8080/



Pour récupérer les logs de connection:

docker cp $(docker ps -q -f name=microserviceprojet):/app/api/src/logs_login.csv ./api/src/logs_login.csv



Les utilisateurs de base se trouvent dans le .env