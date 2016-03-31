// steal this file from https://github.com/bsphere/celery/blob/master/celery.go
// Package celery provides a Golang client library for
// calling Celery tasks using an AMQP backend,
// it depends on channels created by http://github.com/streadway/amqp,
//
// for additional info see http://www.celeryproject.org
package hera

import (
	"encoding/json"
	"github.com/streadway/amqp"
	"time"
)

// Celery task representation,
// Task - task name,
// Id - task UUID,
// Args - optional task args,
// KWArgs - optional task kwargs,
// Retries - optional number of retries,
// ETA - optional time for a scheduled task,
// Expires - optional time for task expiration
type Task struct {
	Task    string
	Id      string
	Args    []interface{}
	KWArgs  map[string]interface{}
	Retries int
	ETA     time.Time
	Expires time.Time
}

const timeFormat = "2006-01-02T15:04:05.999999Z"

// Returns a pointer to a new task object
func NewTask(
	task string,
	id string,
	args []interface{},
	kwargs map[string]interface{},
) *Task {
	return &Task{
		Task:   task,
		Id:     id,
		Args:   args,
		KWArgs: kwargs,
	}
}

// Marshals a Task object into JSON bytes array,
// time objects are converted to UTC and formatted in ISO8601
func (t *Task) MarshalJSON() ([]byte, error) {
	type FormattedTask struct {
		Task    string                 `json:"task"`
		Id      string                 `json:"id"`
		Args    []interface{}          `json:"args,omitempty"`
		KWArgs  map[string]interface{} `json:"kwargs,omitempty"`
		Retries int                    `json:"retries,omitempty"`
		ETA     string                 `json:"eta,omitempty"`
		Expires string                 `json:"expires,omitempty"`
	}

	out := FormattedTask{
		Task:    t.Task,
		Id:      t.Id,
		Args:    t.Args,
		KWArgs:  t.KWArgs,
		Retries: t.Retries,
	}

	if !t.ETA.IsZero() {
		out.ETA = t.ETA.UTC().Format(timeFormat)
	}

	if !t.Expires.IsZero() {
		out.Expires = t.Expires.UTC().Format(timeFormat)
	}

	return json.Marshal(out)
}

// Publish a task to an AMQP channel,
// default exchange is "",
// default routing key is "celery"
func (t *Task) Publish(ch *amqp.Channel, exchange, key string) error {
	body, err := json.Marshal(t)
	if err != nil {
		return err
	}

	msg := amqp.Publishing{
		DeliveryMode:    amqp.Persistent,
		Timestamp:       time.Now(),
		ContentType:     "application/json",
		ContentEncoding: "utf-8",
		Body:            body,
	}

	return ch.Publish(exchange, key, false, false, msg)
}
