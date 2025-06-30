TARGET := testTemplate

CXX := g++
CXXFlags := -std=c++17 -Wall

.PHONY: build
build: $(TARGET)

.PHONY: run
run: $(TARGET)
	./$(TARGET)

.PHONY: clean
clean:
	rm -rf $(TARGET)

$(TARGET) : main.cpp parser.cpp
	$(CXX) $(CXXFlags) -o $@ $^
