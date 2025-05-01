
CREATE OR ALTER PROC interface.ObterCoberturasAtivas(@CodigoAmbiente INT, @CodigoUsuario INT)
AS
BEGIN

	SELECT 
		[type] = 'text',
		[text] = CONCAT('Beneficio:', be.Nome, ', ', 
				'Plano:', fa.Nome,', ', 
				'Fornecedor:', fo.Nome,', ', 
				'Valor: ', FORMAT(co.ValorBeneficio, 'C', 'pt-BR'), ', ',
				'Início Vigência: ', FORMAT(co.InicioVigencia, 'dd/MM/yyyy'), ', ',
				CASE WHEN co.TerminoVigencia IS NOT NULL THEN CONCAT('Término Vigência: ', FORMAT(co.TerminoVigencia, 'dd/MM/yyyy'), ', ') ELSE '' END,
				'Custo Reais: ', FORMAT((ISNULL(co.CustoReaisTitular, 0) + ISNULL(co.CustoReais, 0)), 'C', 'pt-BR'), ', ',
				'Custo Pontos: ', FORMAT((ISNULL(co.CustoPontosTitular, 0) + ISNULL(co.CustoPontos, 0)), 'N', 'pt-BR'), ', ',
				'Código: ', co.Codigo)
	FROM 
		beneficios.Beneficio be 
		JOIN beneficios.Cobertura co ON co.CodigoBeneficio = be.Codigo
		JOIN beneficios.Funcionario fu ON fu.Codigo = co.CodigoFuncionario
		JOIN cadastro.Pessoa pe ON pe.Codigo = fu.CodigoPessoa
		JOIN beneficios.Faixa fa ON fa.Codigo = co.CodigoFaixa AND fa.Nenhum = 0
		JOIN beneficios.Fornecedor fo ON fo.Codigo = co.CodigoFornecedor
	WHERE
		pe.CodigoAmbiente=@CodigoAmbiente
	AND pe.CodigoUsuario=@CodigoUsuario
	AND co.InicioVigencia <= GETDATE()
	AND(co.TerminoVigencia > GETDATE() OR co.TerminoVigencia IS NULL)
	ORDER BY
		be.Nome,
		fa.Nome,
		fo.Nome,
		co.Codigo
END
GO

CREATE OR ALTER PROC interface.ObterBeneficiariosPorCobertura(@Codigo INT)
AS
BEGIN

	SELECT 
		[type] = 'text',
		[text] = CONCAT('Nome: ', pe.Nome, 
		', CPF: ', geral.formatarCpf(pe.CPF),
		', Nascimento: ', FORMAT(pe.Nascimento, 'dd/MM/yyyy'),
		', Parentesco: Titular')
	FROM 
		beneficios.Cobertura co
		JOIN beneficios.Funcionario fu ON fu.Codigo = co.CodigoFuncionario
		JOIN cadastro.Pessoa pe ON pe.Codigo = fu.CodigoPessoa
	WHERE
	--	pe.CodigoAmbiente=@CodigoAmbiente
	--AND pe.CodigoUsuario=@CodigoUsuario
		co.Codigo = @Codigo
	UNION
	SELECT 
		[type] = 'text',
		[text] = CONCAT('Nome: ', de.Nome, 
		', CPF: ', geral.formatarCpf(de.CPF),
		', Nascimento: ', FORMAT(de.Nascimento, 'dd/MM/yyyy'),
		', Parentesco: ', gp.Descricao)
	FROM 
		beneficios.Cobertura co
		JOIN beneficios.Funcionario fu ON fu.Codigo = co.CodigoFuncionario
		JOIN cadastro.Pessoa pe ON pe.Codigo = fu.CodigoPessoa
		JOIN beneficios.CoberturaDependente cd ON cd.CodigoCobertura = co.Codigo
		JOIN beneficios.Dependente de ON de.Codigo = cd.CodigoDependente
		JOIN cadastro.GrauParentesco gp ON gp.Codigo = de.CodigoGrauParentesco
	WHERE
	--	pe.CodigoAmbiente=@CodigoAmbiente
	--AND pe.CodigoUsuario=@CodigoUsuario
		co.Codigo = @Codigo
		
END
GO

/*
exec interface.ObterSolicitacoesPendentes @CodigoUsuario=324745
*/
CREATE OR ALTER PROC interface.ObterSolicitacoesPendentes(@CodigoUsuario INT)
AS
BEGIN

	SELECT
		[type] = 'text',
		[text] = CONCAT('Tipo: ' , ts.Descricao,
		', Status: ', si.Descricao,
		', Criado em: ', FORMAT(so.Criacao, 'dd/MM/yyyy HH:mm:ss'),
		', Codigo: ', so.Codigo
		)
		INTO #Resultado
	FROM
		solicitacoes.Solicitacao so 
		JOIN solicitacoes.TipoSolicitacao ts ON ts.Codigo = so.CodigoTipo
		LEFT JOIN solicitacoes.Situacao si ON si.Codigo = so.CodigoSituacao
		
	WHERE
		so.CodigoUsuarioSolicitante = @CodigoUsuario
	AND so.Status NOT IN(6, 5, 9)
	ORDER BY
		so.Criacao 


	IF NOT EXISTS(SELECT 1 FROM #Resultado)
		SELECT [type] = 'text', [text] = 'Voce nao possui solicitacoes pendentes'
	ELSE 
		SELECT * FROM #Resultado

END
GO


/*
exec interface.SaldoDisponivelReembolso @CodigoUsuario=324745
*/
CREATE OR ALTER PROC interface.SaldoDisponivelReembolso(@CodigoUsuario INT)
AS
BEGIN
	
	SELECT
		[type] = 'text',
		[text] = FORMAT(sp.Pontos, 'N', 'pt-BR')
		INTO #Resultado
	FROM
		beneficios.Funcionario fu
		JOIN cadastro.Pessoa pe ON pe.Codigo = fu.CodigoPessoa
		JOIN beneficios.GrupoEmpresa ge ON ge.CodigoAmbiente = pe.CodigoAmbiente
		JOIN beneficios.SaldoPontos sp ON sp.AnoMes = ge.AnoMesAtual AND sp.CodigoFuncionario = fu.Codigo
	WHERE
		pe.CodigoUsuario = @CodigoUsuario

	IF NOT EXISTS(SELECT 1 FROM #Resultado)
		SELECT [type] = 'text', [text] = 'Voce nao possui saldo disponivel no periodo!'
	ELSE
		SELECT * FROM #Resultado

END
GO


/*
exec interface.MeusDependentes @CodigoUsuario=324745
*/
CREATE OR ALTER PROC interface.MeusDependentes(@CodigoUsuario INT)
AS
BEGIN
	
	SELECT
		[type] = 'text',
		[text] = CONCAT('Nome: ', de.Nome, 
		', CPF: ', geral.formatarCpf(de.CPF),
		', Nascimento: ', FORMAT(de.Nascimento, 'dd/MM/yyyy'),
		', Parentesco: ', gp.Descricao,
		', Situacao: ', CASE WHEN de.Excluido = 1 THEN 'Excluido' ELSE 'Ativo' END
		)
		INTO #Resultado
	FROM
		beneficios.Funcionario fu
		JOIN cadastro.Pessoa pe ON pe.Codigo = fu.CodigoPessoa
		JOIN beneficios.Dependente de ON de.CodigoFuncionario = fu.Codigo
		JOIN cadastro.GrauParentesco gp ON gp.Codigo = de.CodigoGrauParentesco
	WHERE
		pe.CodigoUsuario = @CodigoUsuario
	ORDER BY
		pe.Nascimento
	
	IF NOT EXISTS(SELECT 1 FROM #Resultado)
		SELECT [type] = 'text', [text] = 'Voce nao dependentes cadastrados!'
	ELSE
		SELECT * FROM #Resultado
END
GO

