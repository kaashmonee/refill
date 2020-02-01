import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable()
export class MapsProvider {

  host : string = "13.58.236.117";

  constructor(public http: HttpClient) {}

  getAllWaters() {
    let promise = new Promise((resolve, reject) => {
      this.http.get(this.host + '/all').subscribe((data) => {
        resolve(data);
      }, (err) => {
        reject();
      });
    });

    return promise;
  }

  updateRating(oid : string, rating : number) {
    let headers = { "headers": new HttpHeaders({'Content-Type': 'application/json'})};
    let body = { "id": oid, "rating" : rating };
    return this.http.post(this.host + '/update_rating', body, headers);
  }

  /** image is base64 encoded */
  newLocation(name : string, lat : number, long : number, rating : number, image : string ) {
    let headers = { "headers": new HttpHeaders({'Content-Type': 'application/json'})};
    let body = {
      "name": name,
      "lat": lat,
      "long": long,
      "gross_rating": rating,
      "image": image
    };

    return this.http.post(this.host + '/new', body, headers);
  }

}
