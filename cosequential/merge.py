from cosequential.reader import PostingListReader


def intersect(reader1: PostingListReader, reader2: PostingListReader, writer):
    # writer: objeto com write_id(int) que grava em arquivo
    r1 = reader1.next()
    r2 = reader2.next()
    while r1 is not None and r2 is not None:
        if r1 < r2:
            r1 = reader1.next()
        elif r1 > r2:
            r2 = reader2.next()
        else:
            writer.write_id(r1)
            r1 = reader1.next()
            r2 = reader2.next()

def union(reader1: PostingListReader, reader2: PostingListReader, writer):
    r1 = reader1.next()
    r2 = reader2.next()
    while r1 is not None and r2 is not None:
        if r1 < r2:
            writer.write_id(r1)
            r1 = reader1.next()
        elif r1 > r2:
            writer.write_id(r2)
            r2 = reader2.next()
        else:
            writer.write_id(r1)
            r1 = reader1.next()
            r2 = reader2.next()
    while r1 is not None:
        writer.write_id(r1)
        r1 = reader1.next()
    while r2 is not None:
        writer.write_id(r2)
        r2 = reader2.next()