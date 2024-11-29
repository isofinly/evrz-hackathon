import {Something} from './something';

function hello(name: string): string {
    const greeting = 'Hello';
    return `${greeting} ${name}!`;
}

class Example {
    private value: number;

    constructor(value: number) {
        this.value = value;
    }

    getValue(): number {
        return this.value;
    }
}