package main

import (
    "../go-hera/hera"
    "fmt"
)

func main() {
    heraClient, err := hera.NewHera("amqp://celery:celery@192.168.1.9:5672/celery")
    if err != nil {
        panic(fmt.Sprintln("hera init err due to ", err))
    }
    heraClient.RegisterCallback(
        "i-am-task-id",
        "http://baidu.com",
        "GET",
        "",
        []int{1,10},
        10,
        )
    // for revoke test
    // heraClient.RevokeTask("i-am-task-id")
}
