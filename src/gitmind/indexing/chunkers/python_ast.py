import ast

from gitmind.models import Chunk

MAX_CLASS_LINES = 60


def _start_line(node) -> int:
    decorators = getattr(node, "decorator_list", [])
    return min([node.lineno] + [d.lineno for d in decorators])


def _make_chunk(repo_id, path, lines, name, kind, start, end) -> Chunk:
    return Chunk(
        repo_id=repo_id,
        path=path,
        symbol_name=name,
        symbol_type=kind,
        start_line=start,
        end_line=end,
        language="python",
        text="\n".join(lines[start - 1 : end]),
    )


def _chunk_class(node, repo_id, path, lines) -> list[Chunk]:
    start = _start_line(node)
    end = node.end_lineno
    methods = [
        n for n in node.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    if end - start + 1 <= MAX_CLASS_LINES or not methods:
        return [_make_chunk(repo_id, path, lines, node.name, "class", start, end)]

    chunks = [
        _make_chunk(repo_id, path, lines, node.name, "class",
                    start, _start_line(methods[0]) - 1)
    ]
    for method in methods:
        chunks.append(
            _make_chunk(repo_id, path, lines, f"{node.name}.{method.name}",
                        "method", _start_line(method), method.end_lineno)
        )
    return chunks


def chunk_python(content: str, path: str, repo_id: str) -> list[Chunk]:
    tree = ast.parse(content)
    lines = content.splitlines()

    chunks: list[Chunk] = []
    module_nodes = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            chunks.append(
                _make_chunk(repo_id, path, lines, node.name, "function",
                            _start_line(node), node.end_lineno)
            )
        elif isinstance(node, ast.ClassDef):
            chunks.extend(_chunk_class(node, repo_id, path, lines))
        else:
            module_nodes.append(node)

    if module_nodes:
        text = "\n".join(
            "\n".join(lines[n.lineno - 1 : n.end_lineno]) for n in module_nodes
        )
        chunks.append(
            Chunk(
                repo_id=repo_id,
                path=path,
                symbol_name="<module>",
                symbol_type="module",
                start_line=module_nodes[0].lineno,
                end_line=module_nodes[-1].end_lineno,
                language="python",
                text=text,
            )
        )

    return chunks