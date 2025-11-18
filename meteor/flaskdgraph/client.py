from flask import current_app, g
import pydgraph



class DGraph(object):
    # Class for dgraph database connection

    def init_app(self, app):
        self.app = app

        if "dgraph" in app.extensions and "stub" in app.extensions["dgraph"]:
            app.logger.warning("DGraph extension already initialized for this app.")
            return

        app.extensions.setdefault("dgraph", {})

        app.extensions["dgraph"]["stub"] = pydgraph.DgraphClientStub(
            app.config.get("DGRAPH_ENDPOINT", "localhost:9080"),
            credentials=app.config.get("DGRAPH_CREDENTIALS", None),
            options=app.config.get("DGRAPH_OPTIONS", None),
        )

        app.teardown_appcontext(self.teardown)

    # create a/ get the connection
    @property
    def connection(self):
        if not hasattr(g, "dgraph_client"):
            current_app.logger.debug(
                f"Establishing connection to DGraph: {current_app.config.get('DGRAPH_ENDPOINT')}"
            )

            dgraph_stub = current_app.extensions.get("dgraph", {}).get("stub")

            if dgraph_stub is None:
                raise RuntimeError(
                    "DGraph client stub is not initialized. Ensure init_app has been called."
                )

            g.dgraph_client = pydgraph.DgraphClient(dgraph_stub)

        return g.dgraph_client

    # create a/ get the transaction
    @property
    def txn(self):
        if not hasattr(g, "dgraph_txn"):
            g.dgraph_txn = self.connection.txn()

        return g.dgraph_txn

    # teardown at the end of each request, commit transaction if no exception, discard if exception -> atomical requests
    def teardown(self, exception):
        txn = g.pop("dgraph_txn", None)
        if txn is not None:
            if exception is None:
                try:
                    txn.commit()
                except Exception as e:
                    current_app.logger.error(f"Error committing DGraph transaction: {e}")
                    txn.discard()
            else:
                current_app.logger.info(
                    f"Discarding transaction due to request exception: {exception}"
                )
                txn.discard()
