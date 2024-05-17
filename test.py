import re
import datetime as dt


def character_count_by_sec(text):
    """
    :param text: raw text with the following format:
        <start_time> --> <end_time>
        <subtitle>
        Example:
            00:01:36:05 --> 00:01:37:22
            hacen de la política.
    :return: int => characters per second (cps)
    """
    def compute_time_diff_in_seconds():
        start_time, end_time = time_line.split("-->")
        start_time = dt.datetime.strptime(f'{start_time.strip()}', "%H:%M:%S.%f")
        end_time = dt.datetime.strptime(f'{end_time.strip()}', "%H:%M:%S.%f")
        num_seconds = round((end_time - start_time).total_seconds())
        return num_seconds

    new_blocs = []
    break_blocs = re.split(r"(?:\r?\n){2,}", text.strip())
    for bloc in break_blocs:
        bloc_lines = bloc.split('\n')
        time_line = bloc_lines[0]
        subtitle = ''.join(bloc_lines[1:])
        subtitle_time_elapsed = compute_time_diff_in_seconds()
        subtitle_num_chars = len(subtitle.replace(" ", "").strip())
        cps = subtitle_num_chars/max(subtitle_time_elapsed, 1)
        new_blocs.append(f"{bloc}\ncps: {cps}\nchars: {subtitle_num_chars}")

    return '\n'.join(new_blocs)

if __name__ == '__main__':
