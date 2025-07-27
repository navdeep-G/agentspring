from h2o_wave import main, app, Q, ui
import requests
import time

API_URL = "http://localhost:8000"
API_KEY = "demo-key"
ROLE = "user"

@app('/complaint')
async def serve(q: Q):
    if not q.client.initialized:
        q.page['form'] = ui.form_card(box='1 1 4 4', items=[
            ui.textbox(name='customer_id', label='Customer ID', value='acme'),
            ui.textbox(name='complaint', label='Complaint Text', multiline=True),
            ui.buttons([
                ui.button(name='analyze', label='Analyze', primary=True)
            ])
        ])
        q.client.initialized = True
        await q.page.save()
        return

    if q.args.analyze:
        customer_id = q.args.customer_id
        complaint = q.args.complaint
        q.page['result'] = ui.markdown_card(
            box='1 5 4 2',
            title='Status',
            content='Submitting complaint for analysis...'
        )
        await q.page.save()

        # Submit async request
        resp = requests.post(
            f"{API_URL}/analyze_async",
            headers={
                "x-api-key": API_KEY,
                "x-role": ROLE,
                "Content-Type": "application/json"
            },
            json={"customer_id": customer_id, "message": complaint}
        )
        if resp.status_code == 200:
            data = resp.json()
            tenant_id = "default"  # Use the only pre-created tenant for demo/dev
            status_url = f"{API_URL}/tenants/{tenant_id}/tasks/{data['task_id']}/status"
            # Poll for result
            import datetime
            start_time = datetime.datetime.now()
            result_found = False
            for attempt in range(60):
                try:
                    status_resp = requests.get(
                        status_url,
                        headers={"x-api-key": API_KEY, "x-role": ROLE}
                    )
                    elapsed = (datetime.datetime.now() - start_time).seconds
                    if status_resp.status_code == 404:
                        q.page['result'].content = (
                            f"Waiting for your analysis to begin...<br/>"
                            f"Elapsed time: {elapsed} seconds"
                        )
                    elif status_resp.status_code == 200:
                        try:
                            status_data = status_resp.json()
                        except Exception as parse_err:
                            q.page['result'].content = (
                                f"Received invalid JSON from backend: {parse_err}\n"
                                f"Raw response: {status_resp.text}"
                            )
                            await q.page.save()
                            break
                        status = status_data.get("status")
                        if status == "SUCCESS" and status_data.get("result"):
                            q.page['result'].content = (
                                f"**Analysis complete!**\n\n```json\n{status_data['result']}\n```"
                            )
                            await q.page.save()
                            result_found = True
                            break
                        elif status == "FAILURE":
                            q.page['result'].content = (
                                f"**Analysis failed:** {status_data.get('error')}"
                            )
                            await q.page.save()
                            break
                        else:
                            q.page['result'].content = (
                                f"Task is running (status: {status}).<br/>"
                                f"Elapsed time: {elapsed} seconds"
                            )
                    else:
                        q.page['result'].content = (
                            f"Unexpected response from backend: {status_resp.status_code}<br/>"
                            f"Body: {status_resp.text}"
                        )
                    await q.page.save()
                except Exception as e:
                    q.page['result'].content = f"Error polling status: {str(e)}"
                    await q.page.save()
                    break
                time.sleep(2)
            if not result_found:
                q.page['result'].content = (
                    "Timed out waiting for result.<br/>"
                    "If this happens repeatedly, check that your Celery worker is running and healthy."
                )
                await q.page.save()
        else:
            q.page['result'].content = f"Failed to submit task: {resp.text}"
            await q.page.save()
