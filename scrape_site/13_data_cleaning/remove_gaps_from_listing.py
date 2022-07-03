# open file
import csv
from _csv import reader
import globalfunction.vv as vv  # importing


def clean_file(in_file="testlist.txt", out_file=None):
    removable_ids = ['11111111', '222222222']

    if in_file and not out_file:
        out_file = in_file.replace(".csv", "_out.csv").replace(".txt", "_out.txt")
        if in_file == out_file:
            out_file = "accounts.txt"

    # skip the first line(the header)
    with open(in_file, 'r') as in_file, open(out_file, "w") as csv_out_file:
        file_csv_reader = reader(in_file)
        writer = csv.writer(csv_out_file, delimiter=',')
        head = next(file_csv_reader)
        # csv_out_file.write(head)
        writer.writerow(head)
        expected_columns = len(head)
        headers = head

        # check if the file is empty or not
        index = 0
        # Iterate over each row
        for line in file_csv_reader:
            if index > 50000:
                pass
            else:
                if line[0] in removable_ids:
                    print(f'unexpected col count at {index}')
                    print(line)
                    print(f'warning, index {index} is in removable ids list')
                else:
                    out_line = ",".join(line) + "\n"
                    # csv_out_file.writelines(out_line)
                    writer.writerow(line)

            index += 1
        #                my_line = in_file.readline()
        quit()


clean_file(vv.LISTING_BASIC_FILE)