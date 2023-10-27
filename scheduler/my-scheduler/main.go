package main

import (
	"k8s.io/kubernetes/cmd/kube-scheduler/app"
	"myschedular/plugins/scorebylabel"
)

func main() {
	command := app.NewSchedulerCommand(
		app.WithPlugin(scorebylabel.Name, scorebylabel.New))
	command.Execute()
}
