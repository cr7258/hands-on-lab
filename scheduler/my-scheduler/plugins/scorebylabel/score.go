package scorebylabel

import (
	"context"
	"fmt"
	v1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/klog/v2"
	"k8s.io/kubernetes/pkg/scheduler/framework"
	"strconv"
)

const (
	Name                     = "ScoreByLabel"
	LabelKey                 = "score-by-label"
	DefaultMissingLabelScore = 0
)

var _ framework.ScorePlugin = &ScoreByLabel{}

type ScoreByLabel struct {
	handle framework.Handle
}

func (s *ScoreByLabel) Score(ctx context.Context, state *framework.CycleState, p *v1.Pod, nodeName string) (int64, *framework.Status) {
	nodeInfo, err := s.handle.SnapshotSharedLister().NodeInfos().Get(nodeName)
	if err != nil {
		return 0, framework.NewStatus(framework.Error, fmt.Sprintf("error getting node information: %s", err))
	}
	nodeLabels := nodeInfo.Node().Labels

	if val, ok := nodeLabels[LabelKey]; ok {
		scoreVal, err := strconv.ParseInt(val, 10, 64)
		if err != nil {
			klog.V(4).InfoS("unable to parse score value from node labels", LabelKey, "=", val)
			klog.V(4).InfoS("use the default score", DefaultMissingLabelScore, " for node with labels not convertable to int64!")
			return DefaultMissingLabelScore, nil
		}

		klog.Infof("[ScoreByLabel] Label score for node %s is %s = %v", nodeName, LabelKey, scoreVal)

		return scoreVal, nil
	}
	return DefaultMissingLabelScore, nil
}

func (s *ScoreByLabel) NormalizeScore(ctx context.Context, state *framework.CycleState, p *v1.Pod, scores framework.NodeScoreList) *framework.Status {
	var higherScore int64
	higherScore = framework.MinNodeScore
	for _, node := range scores {
		if higherScore < node.Score {
			higherScore = node.Score
		}
	}

	for i, node := range scores {
		if higherScore > 0 {
			scores[i].Score = node.Score * framework.MaxNodeScore / higherScore
		}
	}

	klog.Infof("[ScoreByLabel] Nodes final score: %v", scores)
	return nil
}

func (s *ScoreByLabel) ScoreExtensions() framework.ScoreExtensions {
	return s
}

func (*ScoreByLabel) Name() string {
	return Name
}

func New(obj runtime.Object, h framework.Handle) (framework.Plugin, error) {
	return &ScoreByLabel{
		handle: h,
	}, nil
}
