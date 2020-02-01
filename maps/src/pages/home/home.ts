import { Component, ViewChild } from '@angular/core';
import { GoogleMapsComponent } from '../../components/google-maps/google-maps';
import { MapsProvider } from '../../providers/maps/maps';

@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage {

    @ViewChild(GoogleMapsComponent) mapComponent: GoogleMapsComponent;

    constructor(public mp : MapsProvider) {

    }

    ionViewDidLoad() {
      this.mapComponent.start().then(() => {
      	this.mp.getAllWaters().then((data:any[]) => {
	  for (var i = 0; i < data.length; i++)
	  {

            this.mapComponent.addMarker(data[i]["latitude"], data[i]["longitude"], data[i]["name"],
				       data[i]["image"], data[i]["gross_rating"], data[i]["num_votes"]);
	  }
          console.log(data);
        }, (err) => {
          // IDK, this is a yikes
        });
      });
    }
}
