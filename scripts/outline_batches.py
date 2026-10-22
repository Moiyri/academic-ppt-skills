"""Return consecutive page groups for image-generation storyboard prompts."""
import argparse
import json


def batches(total):
    if isinstance(total, bool) or not isinstance(total, int) or total < 1:
        raise ValueError('total must be a positive integer')
    return [list(range(start, min(start + 8, total + 1)))
            for start in range(1, total + 1, 8)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('total', type=int)
    args = parser.parse_args()
    print(json.dumps(batches(args.total)))
