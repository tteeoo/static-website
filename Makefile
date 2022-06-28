title = Theo Henson
url = https://theohenson.com

.PHONY: build clean poem

poem: build
	./new_poem.py
build: dst
	./ssg6 src dst "${title}" "${url}"
	./blog_feeds.py
dst:
	mkdir dst
clean:
	rm -rfv dst/*
	rm -fv dst/.files
