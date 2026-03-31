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

ou sinon

USERS

jean.dupont@email.com
password123

sophie.martin@email.com
password456

luc.vaillant@email.com
password789


ADMIN

admin1@email.com
adminpass1

admin2@email.com
adminpass2
