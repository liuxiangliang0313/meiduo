# coding:utf8

# 设置broker对象的
# broker_url 我们采用的是 Redis 当我们有任务之后,这个任务发送到 redis所在的 14号库
broker_url = "redis://127.0.0.1/14"

# 我们将执行结果保存在 redis的 15号库中
result_backend = "redis://127.0.0.1/15"
