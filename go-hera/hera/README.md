# go-hera

go-hera 是hera的golang库，封装了hera接口

## 优点

- 支持传入用","分割的mq地址
- 支持自动failover
- 支持mq自动重连

## 用法

```
import github.com/liutaihua/hera/go-hera/hera

heraClient, err := hera.NewHera(mqURL)
if err != nil {
    panic(fmt.Sprintln("hera init err due to ", err))
}
heraClient.RegisterCallback(
    "i-am-task-id",     // task-id
    "http://baidu.com", // callback url
    "GET",          // callback method
    "",             // callback data
    []int{1,10},    // retry args
    30              // countdown
    true            // UTC enable
    )
// utc参数应当始终为true, 除非hera改变了eta的时间方式
```
