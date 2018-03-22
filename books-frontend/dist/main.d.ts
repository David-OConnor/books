export interface Author {
    id: number;
    first_name: string;
    last_name: string;
}
export interface Book_ {
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
