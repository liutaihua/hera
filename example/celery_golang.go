package main

import (
    "../go-hera"
    "fmt"
)

func main() {
    heraClient, err := hera.NewHera("amqp://guest")
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
        true)
}
// 使用 hera/go-hera库