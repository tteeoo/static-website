title = Theo Henson
url = https://theohenson.com

.PHONY: build clean 

build: dst
	./ssg6 src dst "${title}" "${url}"
	./feeds.py
dst:
	mkdir dst
clean:
	rm -rfv dst/*
	rm -fv dst/.files
