/// <reference types="react" />
export interface Author {
    id: number;
    first_name: string;
    last_name: string;
}
export interface Book2 {
    id: number;
    title: string;
    author: Author;
    description: string;
    wikipedia_url: string;
    gutenberg_url: string;
    adelaide_url: string;
    amazon_url: string;
    kobo_url: string;
    google_url: string;
    copyright_exp_us: string;
    copyright_expired: boolean;
    isbn_10: string;
    isbn_13: string;
}
export declare const Main: ({ store, gstore }: {
    store: any;
    gstore: any;
}) => JSX.Element;
export declare function get(url: string, callback?: any): void;
export default Main;
