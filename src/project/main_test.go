package main

import (
	"testing"
)

func TestDummy(t *testing.T) {
	a := "test"
	c := dummyString(a)

	if a != c {
		t.Error("a should equal b")
	}
}
