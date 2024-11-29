const userManager = {
  userName: "John",
  userAge: 25,

  printInfo: () => {
    console.log(`Name: ${this.userName}, Age: ${this.userAge}`);
  },

  updateAge: (newAge) => {
    this.userAge = newAge;
  },
};

class BadUserClass {
  private name: string = "Jane";

  getName = () => {
    return this.name;
  };

  setName = (newName: string) => {
    this.name = newName;
  };
}
