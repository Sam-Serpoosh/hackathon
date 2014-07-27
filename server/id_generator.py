class IdGenerator:
  def __init__(self, filename):
    self.filename = filename

  def generate_id(self):
    content_lines = self.read_file_lines()
    latest_record = content_lines[-1]
    attributes = latest_record.split(",")
    try:
      new_id = int(attributes[0]) + 1
      return new_id
    except ValueError:
      return 1

  def read_file_lines(self):
    f = open(self.filename, "r")
    lines = f.readlines()
    f.close()
    return lines

