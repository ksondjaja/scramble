

export function Question(title, category, content, options) {

    this.title = title;
    this.category = category;
    this.content = content;
    this.options = options;

}

export function Option(content, is_correct) {

    this.content = content;
    this.is_correct = is_correct;

}
