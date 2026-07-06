var DB, PROMISE, get_demo_database, request;
PROMISE = null;
DB = null;
get_demo_database = async function flx_get_demo_database (module) {
    var PROMISE, initDatabase, todoSchema;
    if ((!_pyfunc_truthy(PROMISE))) {
        todoSchema = ({version: 0, primaryKey: "id", type: "object", properties: ({id: ({type: "string", maxLength: 36}), title: ({type: "string"}), done: ({type: "boolean"}), createdAt: ({type: "string", format: "date-time"})}), required: ["title", "done"]});
        initDatabase = (async function flx_initDatabase () {
            var _pre_insert;
            if ((!_pyfunc_truthy(DB))) {
                DB = await module.createRxDatabase(({name: "pytigon_demo", storage: module.getRxStorageDexie()}));
                await DB.addCollections(({todos: ({schema: todoSchema})}));
                _pre_insert = (function flx__pre_insert (docData) {
                    if ((!_pyfunc_truthy(docData.id))) {
                        docData.id = window.v7();
                    }
                    if ((!_pyfunc_truthy(docData.createdAt))) {
                        docData.createdAt = ((new Date()).toISOString)();
                    }
                    return null;
                }).bind(this);

                DB.todos.preInsert(_pre_insert);
            }
            return DB;
        }).bind(this);

        PROMISE = initDatabase();
    }
    return PROMISE;
};

request = function flx_request (param, complete) {
    var on_load;
    on_load = (function flx_on_load (module) {
        var on_error, test2;
        on_error = (function flx_on_error (err) {
            console.error(err);
            return null;
        }).bind(this);

        test2 = (function flx_test2 (db) {
            var go, test, uncompletedTodos;
            uncompletedTodos = null;
            test = (async function flx_test () {
                var insertResult, newTodos, row, stub1_seq, stub2_itr, table, table2, uncompletedTodos;
                newTodos = [({title: "Buy groceries", isCompleted: false}), ({title: "Read RxDB documentation", isCompleted: true})];
                insertResult = await db.todos.bulkInsert(newTodos);
                uncompletedTodos = await ((_pymeth_find.call(db.todos, (({selector: ({isCompleted: false})})))).exec)();
                table = Array.prototype.slice.call(uncompletedTodos);
                table2 = [];
                stub1_seq = table;
                if ((typeof stub1_seq === "object") && (!Array.isArray(stub1_seq))) { stub1_seq = Object.keys(stub1_seq);}
                for (stub2_itr = 0; stub2_itr < stub1_seq.length; stub2_itr += 1) {
                    row = stub1_seq[stub2_itr];
                    console.log("- ", row.id, row.title, row.createdAt);
                    _pymeth_append.call(table2, ({id: row.id, title: row.title, createdAt: row.createdAt, isCompleted: row.isCompleted}));
                }
                return table2;
            }).bind(this);

            go = (function flx_go (table) {
                var context;
                console.log(table);
                context = ({template: ".", table: table});
                complete(context);
                return null;
            }).bind(this);

            (test().then)(go);
            return null;
        }).bind(this);

        (get_demo_database(module).then)(test2);
        return null;
    }).bind(this);

    window.jsimp("http://127.0.0.1:8000/static/_schcomponents/rxdb/rxdb.js", on_load);
    return null;
};

export {request};