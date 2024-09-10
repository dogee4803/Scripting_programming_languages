import requests


# ЗАДАНИЕ 1
get_response = requests.get("https://jsonplaceholder.typicode.com/posts").json()

print("Вывод всех постов с чётным значением userId")
for i in get_response:
    if i["userId"] % 2 == 0:
        print(i)
    

# ЗАДАНИЕ 2
data = {
    "title": "Тестовый пост",
    "body": "Тестовое тело",
    "userId": 4242
}

post_response = requests.post("https://jsonplaceholder.typicode.com/posts", data=data).json()

print(f"Созданный новый пост = {post_response}")
        
        
# ЗАДАНИЕ 3
data1 = {
    "id": 1,
    "title": "Обновлённый пост",
    "userId": 4242
}

put_response = requests.put("https://jsonplaceholder.typicode.com/posts/1", data=data1).json()

print(f"Обновлённый первый пост = {put_response}")
