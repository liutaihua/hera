package hera

import (
	"errors"
	"fmt"
	"github.com/streadway/amqp"
	"log"
	"strings"
	"time"
)

const (
    REGISTER_CALLBACK_NAME = "handler.timer.register_callback"
    REVOKE_TASK_NAME = "handler.task_controller.revoke_manual"
    )

type Hera struct {
	url      string // mq url
	exchange string // mq exhcnage key
	routing  string // mq routing key
	conn     *amqp.Connection
}

func NewHera(url string) (*Hera, error) {
	hera := &Hera{
		url: url,
	}

	if err := hera.Dial(); err != nil {
		log.Fatalln("mq connection error due to", err)
		return nil, err
	}

	go hera.Monitor()
	return hera, nil
}

func (hera *Hera) Dial() error {

	for _, url := range strings.Split(hera.url, ",") {
		conn, err := amqp.Dial(url)
		if err != nil {
			log.Fatalln("mq dial error due to", err)
		} else {
			hera.conn = conn
			return nil
		}
	}
	return errors.New("Hera dial mq failure")
}

// 自动重连，通过订阅conn的NotifyClose达到自动重连的目的
func (hera *Hera) Monitor() {
	closeCh := hera.conn.NotifyClose(make(chan *amqp.Error))
	go func() {
		for closeErr := range closeCh {
			log.Fatalln("hera mq connection close due to ", closeErr)
			conn, err := amqp.Dial(hera.url)
			if err != nil {
				log.Fatalln("hera redail amqp error due to", err)
			}
			log.Print("hera redail amqp success")
			hera.conn = conn
		}
	}()
}

// 注册回调，通过hera（celery）进行http调用
// url:
// method: GET/POST etc...
// data: POST data
// delay: 延迟执行时间(秒)
func (hera *Hera) RegisterCallback(
	task_id,
	url,
	method,
	data string,
	retryInterval []int,
	delaySecond int) error {
	// 创建task
	task := NewTask(
		REGISTER_CALLBACK_NAME,
		task_id,
		[]interface{}{
			url,
			method,
			data,
			nil,
			retryInterval,
		},
		nil,
	)

	if delaySecond != 0 {
		eta := time.Now().Add(time.Duration(delaySecond) * time.Second)
		task.ETA = eta
	}

	// 打开mq channel
	ch, err := hera.conn.Channel()
	if err == amqp.ErrClosed {
		if err := hera.Dial(); err != nil {
			return errors.New(fmt.Sprintln("hera mq connection err due to", err))
		}
		if ch, err = hera.conn.Channel(); err != nil {
			return errors.New(fmt.Sprintln("hera mq open channel err due to", err))
		}
	}
    defer ch.Close()
	return task.Publish(ch, "", "celery")
}

func (hera *Hera) RevokeTask(task_id string) error {
    task := NewTask(
        REVOKE_TASK_NAME,
        "",
        []interface{} {task_id},
        nil,
    )
	task.ETA = time.Now()

	ch, err := hera.conn.Channel()
	if err == amqp.ErrClosed {
		if err := hera.Dial(); err != nil {
			return errors.New(fmt.Sprintln("hera mq connection err due to", err))
		}
		if ch, err = hera.conn.Channel(); err != nil {
			return errors.New(fmt.Sprintln("hera mq open channel err due to", err))
		}
	}
    defer ch.Close()
	return task.Publish(ch, "", "celery")

}