/*
 * Check a sparse ISO from sparseiso.py with libudfread.
 *
 * Walks the whole UDF tree, prints "DIR path" / "FILE size fnv64 path" in
 * the same order as udfgrab's listing, hashing every file except .EVO, and
 * reports every block libudfread read outside the real ranges listed in
 * <iso>.ranges (a read in a hole means the image misses data the backend
 * needs).
 *
 * cc -O2 -o udfcheck udfcheck.c $(pkg-config --cflags --libs libudfread)
 * ./udfcheck image.iso
 */
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include <udfread/udfread.h>
#include <udfread/blockinput.h>

#define BLOCK 2048

struct range { uint64_t start, end; };

static struct range *ranges;
static size_t range_count;
static unsigned long hole_reads;

struct file_input {
    udfread_block_input input;
    FILE *fp;
};

static int covered(uint64_t start, uint64_t end)
{
    for (size_t i = 0; i < range_count; i++) {
        if (ranges[i].start <= start && start < ranges[i].end) {
            if (end <= ranges[i].end)
                return 1;
            start = ranges[i].end;
            i = (size_t)-1;
        }
    }
    return 0;
}

static int input_read(udfread_block_input *in, uint32_t lba, void *buf, uint32_t n, int flags)
{
    struct file_input *f = (struct file_input *)in;
    (void)flags;
    for (uint32_t i = 0; i < n; i++) {
        uint64_t s = (uint64_t)(lba + i) * BLOCK;
        if (!covered(s, s + BLOCK)) {
            if (hole_reads < 20)
                printf("HOLE lba %" PRIu32 "\n", lba + i);
            hole_reads++;
        }
    }
    if (fseeko(f->fp, (off_t)lba * BLOCK, SEEK_SET))
        return 0;
    return (int)fread(buf, BLOCK, n, f->fp);
}

static uint32_t input_size(udfread_block_input *in)
{
    struct file_input *f = (struct file_input *)in;
    fseeko(f->fp, 0, SEEK_END);
    return (uint32_t)(ftello(f->fp) / BLOCK);
}

static uint64_t fnv64(uint64_t h, const uint8_t *p, size_t n)
{
    while (n--) {
        h ^= *p++;
        h *= 0x100000001b3ULL;
    }
    return h;
}

static void walk(udfread *udf, const char *path)
{
    UDFDIR *dir = udfread_opendir(udf, path);
    struct udfread_dirent ent;
    char child[4096];

    if (!dir) {
        printf("ERROR opendir %s\n", path);
        return;
    }
    while (udfread_readdir(dir, &ent)) {
        if (!strcmp(ent.d_name, ".") || !strcmp(ent.d_name, ".."))
            continue;
        snprintf(child, sizeof(child), "%s/%s", strcmp(path, "/") ? path : "", ent.d_name);
        if (ent.d_type == UDF_DT_DIR) {
            printf("DIR %s\n", child);
            walk(udf, child);
            continue;
        }
        UDFFILE *fp = udfread_file_open(udf, child);
        if (!fp) {
            printf("ERROR open %s\n", child);
            continue;
        }
        int64_t size = udfread_file_size(fp);
        uint64_t h = 0xcbf29ce484222325ULL;
        size_t len = strlen(child);
        if (len < 4 || strcasecmp(child + len - 4, ".EVO")) {
            static uint8_t buf[1 << 16];
            ssize_t got;
            int64_t total = 0;
            while ((got = udfread_file_read(fp, buf, sizeof(buf))) > 0) {
                h = fnv64(h, buf, (size_t)got);
                total += got;
            }
            if (total != size)
                printf("ERROR short read %s %" PRId64 "/%" PRId64 "\n", child, total, size);
            printf("FILE %" PRId64 " %016" PRIx64 " %s\n", size, h, child);
        } else {
            printf("FILE %" PRId64 " - %s\n", size, child);
        }
        udfread_file_close(fp);
    }
    udfread_closedir(dir);
}

int main(int argc, char **argv)
{
    char name[4096], line[8192];
    struct file_input in = { { NULL, input_read, input_size }, NULL };

    if (argc != 2) {
        fprintf(stderr, "usage: %s image.iso\n", argv[0]);
        return 2;
    }
    snprintf(name, sizeof(name), "%s.ranges", argv[1]);
    FILE *rf = fopen(name, "r");
    if (!rf) {
        perror(name);
        return 2;
    }
    while (fgets(line, sizeof(line), rf)) {
        uint64_t s, e;
        if (line[0] == '#' || sscanf(line, "%" SCNu64 " %" SCNu64, &s, &e) != 2)
            continue;
        ranges = realloc(ranges, (range_count + 1) * sizeof(*ranges));
        ranges[range_count].start = s;
        ranges[range_count].end = e;
        range_count++;
    }
    fclose(rf);

    in.fp = fopen(argv[1], "rb");
    if (!in.fp) {
        perror(argv[1]);
        return 2;
    }
    udfread *udf = udfread_init();
    if (udfread_open_input(udf, &in.input) < 0) {
        printf("ERROR udfread_open_input\n");
        return 1;
    }
    printf("# volume id %s\n", udfread_get_volume_id(udf));
    walk(udf, "/");
    udfread_close(udf);
    fclose(in.fp);
    free(ranges);
    printf("# hole reads %lu\n", hole_reads);
    return hole_reads != 0;
}
