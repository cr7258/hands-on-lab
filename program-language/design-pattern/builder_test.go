package design_pattern

import "testing"

func TestBuilder1(t *testing.T) {
	builder1 := &Builder1{}
	director := NewDirector(builder1)
	director.Construct()
	result := builder1.GetResult()
	if result != "123" {
		t.Fatalf("Builder1 fail expect 123 acture %s", result)
	}
}

func TestBuilder2(t *testing.T) {
	builder2 := &Builder2{}
	director := NewDirector(builder2)
	director.Construct()
	result := builder2.GetResult()
	if result != 6 {
		t.Fatalf("Builder2 fail expect 6 acture %d", result)
	}
}
