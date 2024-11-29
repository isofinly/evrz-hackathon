const visible = true; // Плохо: должно быть isVisible
const error = false; // Плохо: должно быть hasError
const login = true; // Плохо: должно быть isLoggedIn
const premium = false; // Плохо: должно быть isPremium
const notifications = true; // Плохо: должно быть hasNotifications

// Плохие примеры именования функций, возвращающих boolean
function valid(email: string): boolean {
  // Плохо: должно быть isValid
  return email.includes("@");
}

function admin(user: any): boolean {
  // Плохо: должно быть isAdmin
  return user.role === "admin";
}

function empty(array: any[]): boolean {
  // Плохо: должно быть isEmpty
  return array.length === 0;
}

class UserAccount {
  private blocked: boolean = false; // Плохо: должно быть isBlocked

  public verified(): boolean {
    // Плохо: должно быть isVerified
    return this.emailConfirmed && this.phoneConfirmed;
  }

  public active(): boolean {
    // Плохо: должно быть isActive
    return this.lastLogin > Date.now() - 30 * 24 * 60 * 60 * 1000;
  }
}
