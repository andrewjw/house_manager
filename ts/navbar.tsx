import React from 'react'

interface LatestProps {
    timestamp: number;
    temp_out: number;
}
  
function getTimeFromDate(d: any): string {
    return d["timestamp"].split(" ")[1];
}

class Home extends React.Component<LatestProps> {
    static async getInitialProps(ctx: any): Promise<LatestProps> {
        const recent_res = await fetch('/api/latest');
        const recent_json = await recent_res.json();

        return { timestamp: recent_json.timestamp, temp_out: recent_json.temp_out }
      }
    
      render() {
        let since_last_update = (new Date().getTime()/1000) - this.props.latest.latest;
    
        let last_update_text: string = "Old";
    
        if (since_last_update < 60) {
          last_update_text = "Updated less than a minute ago.";
        } else if (since_last_update < 60 * 60) {
          last_update_text = "Updated " + Math.floor(since_last_update / 60) + " minutes ago."
        } else {
          last_update_text = "Data is stale. Sorry :-("
        }
    
        return (
<nav class="navbar navbar-expand-lg bg-body-tertiary">
    <div class="container-fluid">
        <a class="navbar-brand" href="#">House Manager</a>
    </div>
</nav>
        );
  