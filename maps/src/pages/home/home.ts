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
      mp.getAllWaters().then((data:any[]) => {
	for (var i = 0; i < data.length; i++)
	{
            this.mapComponent.addMarker(data[i]["lat"], data[i]["lng"]);
	}
        console.log(data);
      }, (err) => {
        // IDK, this is a yikes
      });
    }

    testMarker(){

        let center = this.mapComponent.map.getCenter();
        this.mapComponent.addMarker(center.lat(), center.lng());
    }
}
