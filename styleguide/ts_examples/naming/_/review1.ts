// <Review>
// `x` — однобуквенное имя. Переименуйте в более осмысленное, например, `value`.
// </Review>
const x = 10;

// <Review>
// `api_resp` использует snake_case. Переименуйте в camelCase, например, `apiResponse`.
// </Review>
const api_resp = { status: "ok", data: [] };

// <Review>
// `myComponent` нарушает PascalCase. Переименуйте в `MyComponent`.
// </Review>
class myComponent {
  // <Review>
  // `onClick` должен начинаться с handle. Переименуйте в `handleClick`.
  // </Review>
  onClick() {
    console.log("Clicked");
  }
}

// <Review>
// `calc` — неинформативное имя. Используйте, например, `calculateDouble`.
// </Review>
function calc(value: number): number {
  return value * 2;
}

// <Review>
// `ACTIVE` не соответствует camelCase для переменных. Переименуйте в `isActive`.
// </Review>
const ACTIVE = true;

// <Review>
// `api_result` должен использовать PascalCase. Переименуйте в `ApiResult`.
// </Review>
type api_result = {
  // <Review>
  // `user_id` нарушает camelCase. Переименуйте в `userId`.
  // </Review>
  user_id: number;
  // <Review>
  // `user_name` нарушает camelCase. Переименуйте в `userName`.
  // </Review>
  user_name: string;
};

// <Review>
// `$` в `get$Data` нарушает правило нейминга. Переименуйте в `getData`.
// </Review>
const get$Data = () => {
  return { key: "value" };
};
