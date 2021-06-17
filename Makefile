title = Theo Henson
url = https://theohenson.com

build: dst
	./ssg6 src dst "${title}" "${url}"
dst:
	mkdir dst
clean:
	rm -rfv dst/*
	rm -fv dst/.files
.phony: build clean 
