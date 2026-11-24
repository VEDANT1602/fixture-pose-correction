"""Reconstruct physical spacing and filtering results from the stop-level exports."""
import csv
from pathlib import Path
from statistics import mean, median

HERE = Path(__file__).resolve().parent
BLOCKS = (2, 5, 8, 10)
SPANS = (1, 3, 7)
FRAMES = tuple(8 * block + offset for block in BLOCKS for offset in range(8))


def read(name):
    with (HERE / name).open(newline='') as stream:
        return list(csv.DictReader(stream))


def indexed(rows, fields, value_field):
    result = {}
    for row in rows:
        key = tuple(row[field] for field in fields)
        if key in result:
            raise ValueError(f'Duplicate result for {key}')
        result[key] = float(row[value_field])
    return result


def check():
    robot = indexed(read('robot_bench_errors.csv'), ('frame', 'cells', 'method'), 'residual_deg')
    methods = ('raw', 'static', 'trained', 'assume_095')
    assert len(robot) == len(FRAMES) * len(SPANS) * len(methods)
    table = []
    for span in SPANS:
        row = [mean(abs(robot[str(frame), str(span), method]) for frame in FRAMES)
               for method in methods]
        table.append([round(value, 3) for value in row])
    assert table == [[.377, .393, .373, .463], [.140, .143, .145, .173], [.111, .111, .115, .130]]
    print('Mean absolute disagreement (degrees):', table)

    observations = [row for row in read('reference_sensitivity.csv')
                    if row['omitted_train_block'] == 'none']
    values = indexed(observations, ('frame', 'cells', 'comparison'), 'abs_difference_deg')
    for label, smaller, larger, expected in [
        ('raw_to_full_robot', 1, 3, (.237, .095, 25, .055, .544)),
        ('raw_to_optical', 1, 3, (.279, .298, 26, .171, .551)),
        ('raw_to_full_robot', 3, 7, (.028, .021, 19, .007, .057)),
        ('raw_to_optical', 3, 7, (.029, .044, 21, .015, .047)),
    ]:
        gain = {f: values[str(f), str(smaller), label] - values[str(f), str(larger), label]
                for f in FRAMES}
        block_means = [mean(gain[f] for f in FRAMES if f // 8 == b) for b in BLOCKS]
        result = (round(mean(gain.values()), 3), round(median(gain.values()), 3),
                  sum(x > 0 for x in gain.values()), round(min(block_means), 3),
                  round(max(block_means), 3))
        assert result == expected
        print(label, smaller, larger, result)


if __name__ == '__main__':
    check()
