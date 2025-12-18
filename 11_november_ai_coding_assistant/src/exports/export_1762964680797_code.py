class DatabaseSimulator:
    def __init__(self):
        self.active_transaction = False
        self.temp_count = 0
        self.data = {}
        self.data_count = 0
        self.temp_storage = {}
        self.other_storage = {}

    def begin(self):
        if self.active_transaction:
            temp_dict = self.other_storage | self.temp_storage
            self.other_storage = temp_dict
        self.active_transaction = True

    def get(self, key):
        if key in self.temp_storage:
            return self.temp_storage[key]
        elif key in self.other_storage:
            return self.other_storage[key]
        elif key in self.data:
            return self.data[key]
        else:
            return None

    def set(self, key, value):
        if not self.active_transaction:
            raise Exception("No active transaction")
        else:
            if key in self.other_storage:
                self.other_storage[key] = value
            else:
                self.temp_storage[key] = value

    def count(self):
        return len(self.data.keys())

    def commit(self):
        if not self.active_transaction:
            raise Exception("No active transaction")
        else:
            temp_dict = self.data | self.other_storage | self.temp_storage
            self.data = temp_dict
            self.active_transaction = False

    def rollback(self):
        if not self.active_transaction:
            raise Exception("No active transaction")
        else:
            self.temp_storage = {}
            self.active_transaction = False

if __name__ == "__main__":
    db = DatabaseSimulator()
    db.begin()  # begins a transaction
    print(db.get("a"))  # returns None
    db.set("a", "Hello A")
    print(db.get("a"))  # returns 'Hello A'
    db.set("b", "Hello B")
    print(db.count())  # returns 0
    db.commit()
    print(db.get("a"))  # returns 'Hello A'
    print(db.get("b"))  # returns 'Hello B'
    print(db.count())  # returns 2