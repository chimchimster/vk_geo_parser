# Парсер геолокаций вконтакте

## Установка:
 - Убедитесь, что у вас установлен docker. Выполните команду:

`user@user: docker version`

 - Убедитесь, что у вас установлен git. Выполните команду:

`user@user: git version`

 - Если git и/или docker не установлен, тогда воспользуйтесь официальной документацией

> Docker: https://docs.docker.com/

> Git: https://git-scm.com/doc

Склонируйте репозиторий vk_geo_parser из организации iMAS.

`user@user: git clone <link_to_repository>`

После успешной установки необходимых технологий перейдите в папку проекта на сервере:

`user@user: cd /home/developer/vk_geo/vk_geo_parser/`

Соберите образ проекта:

`user@user: docker build -t vk_geo_parser-actual .`

Создайте репозиторий на [DockerHub](https://hub.docker.com/). Получите токен для работы с вашим репозиторием.
Воспользуйтесь [официальной документацией](https://docs.docker.com/docker-hub/). 

Как только вы получили токен, войдите в свой аккаунт на DockerHub:

`user@user: docker login -u <your login> -p <your dockerhub token>`

Выполните команду:

`user@user: docker tag vk_geo_parser-actual <your repository>`

Затем выполните push команду:

`user@user: docker push <your repository>`

Теперь перейдите в файл docker-compose.yml

`user@user: nano docker-compose.yml`

Найдите следующие строки:

>  image: chimchimster/vk_geo_parser-parser

Это путь до моего образа на DockerHub... NB! Замените его на свой путь!!!

Внимательно посмотрите на docker-compose.yml файл. Внутри есть service tasker. 
Он полностью настроен запускать образ один раз в 30 минут. Образ собирает посты с локаций за последние полчаса.

Чтобы поменять вк токен пересоберите образ и положите в .env файл новый токен.

Выполните команду:

`user@user: docker compose up -d`

Готово! Теперь каждые полчаса парсер будет собирать фотографии с текстом из ВК. Все подробности работы скрипта задокументированы в коде.

Автор: [Артем Касьян](https://github.com/chimchimster) 