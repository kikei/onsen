interface Dict<T> {
  [K: string]: T;
}

export interface JQuery {
  fadeIn(): JQuery;
  fadeOut(): JQuery;
  focus(): JQuery;
  html(): string;
  html(val: string): JQuery;
  show(): JQuery;
  addClass(className: string): JQuery;
  removeClass(className: string): JQuery;
  append(el: HTMLElement): JQuery;
  
  attr(attrName: string): string;
  on(eventName: string, callback: (event:Event) => void): JQuery;
  val(): string;
  val(value: string): JQuery;
}

export declare var $: {
  (el: HTMLElement): JQuery;
  (selector: string): JQuery;
  (readyCallback: () => void ): JQuery;
  ajax(params: any): JQuery;
  param(params: any): string;
}
